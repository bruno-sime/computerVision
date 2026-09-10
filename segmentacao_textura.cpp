#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

constexpr int PATCH_SIZE = 512;
constexpr int FILTER_COUNT = 8;
constexpr int SCALE_COUNT = 3;
constexpr int DESCRIPTOR_SIZE = FILTER_COUNT * SCALE_COUNT;

struct Patch {
    int row;
    int column;
    cv::Mat image;
};

struct DescriptorData {
    cv::Mat values;
    std::vector<Patch> patches;
};

std::vector<cv::Mat> buildFilters() {
    std::vector<cv::Mat> filters;
    filters.emplace_back((cv::Mat_<float>(3, 3) << 1, 2, 1, 0, 0, 0, -1, -2, -1));
    filters.emplace_back((cv::Mat_<float>(3, 3) << 1, 0, -1, 2, 0, -2, 1, 0, -1));
    filters.emplace_back((cv::Mat_<float>(3, 3) << 0, 1, 2, -1, 0, 1, -2, -1, 0));
    filters.emplace_back((cv::Mat_<float>(3, 3) << 2, 1, 0, 1, 0, -1, 0, -1, -2));
    filters.emplace_back((cv::Mat_<float>(3, 3) << 0, 1, 0, 1, -4, 1, 0, 1, 0));

    cv::Mat logKernel(7, 7, CV_32F);
    cv::Mat diffusion(7, 7, CV_32F);
    cv::Mat circular = cv::Mat::zeros(7, 7, CV_32F);
    float logSum = 0.0F;
    float diffusionSum = 0.0F;
    for (int y = -3; y <= 3; ++y) {
        for (int x = -3; x <= 3; ++x) {
            const float radius2 = static_cast<float>(x * x + y * y);
            const float logValue = (radius2 - 4.0F) * std::exp(-radius2 / 8.0F);
            const float diffusionValue = std::exp(-radius2 / 4.0F);
            logKernel.at<float>(y + 3, x + 3) = logValue;
            diffusion.at<float>(y + 3, x + 3) = diffusionValue;
            logSum += logValue;
            diffusionSum += diffusionValue;
            if (radius2 >= 4.0F && radius2 <= 9.0F) {
                circular.at<float>(y + 3, x + 3) = 1.0F;
            }
        }
    }
    logKernel -= logSum / 49.0F;
    diffusion -= diffusionSum / 49.0F;
    circular.at<float>(3, 3) = -static_cast<float>(cv::sum(circular)[0]);
    filters.push_back(logKernel);
    filters.push_back(diffusion);
    filters.push_back(circular);
    return filters;
}

std::vector<Patch> makePatches(const cv::Mat& image, int requested) {
    const int columns = std::min(static_cast<int>(std::sqrt(requested *
        static_cast<double>(image.cols) / image.rows)), image.cols / PATCH_SIZE);
    const int rows = std::min(static_cast<int>(std::ceil(requested / static_cast<double>(std::max(columns, 1)))),
                              image.rows / PATCH_SIZE);
    std::vector<Patch> patches;
    for (int row = 0; row < rows && static_cast<int>(patches.size()) < requested; ++row) {
        for (int column = 0; column < columns && static_cast<int>(patches.size()) < requested; ++column) {
            cv::Rect region(column * PATCH_SIZE, row * PATCH_SIZE, PATCH_SIZE, PATCH_SIZE);
            patches.push_back({row * PATCH_SIZE, column * PATCH_SIZE, image(region).clone()});
        }
    }
    return patches;
}

double meanAbsolute(const cv::Mat& image) {
    return cv::mean(cv::abs(image))[0];
}

DescriptorData extractDescriptors(const cv::Mat& image, int patchCount) {
    const auto filters = buildFilters();
    const auto patches = makePatches(image, patchCount);
    cv::Mat descriptors(static_cast<int>(patches.size()), DESCRIPTOR_SIZE, CV_64F, cv::Scalar(0));
    cv::Mat current = image.clone();
    for (int scale = 0; scale < SCALE_COUNT; ++scale) {
        if (scale > 0) {
            cv::Mat next;
            cv::pyrDown(current, next);
            current = next;
        }
        std::vector<cv::Mat> responses;
        for (const auto& filter : filters) {
            cv::Mat response;
            cv::filter2D(current, response, CV_32F, filter, cv::Point(-1, -1), 0, cv::BORDER_REFLECT101);
            responses.push_back(response);
        }
        const int scaledPatch = PATCH_SIZE >> scale;
        for (int patchIndex = 0; patchIndex < static_cast<int>(patches.size()); ++patchIndex) {
            const int y = patches[patchIndex].row >> scale;
            const int x = patches[patchIndex].column >> scale;
            const cv::Rect region(x, y, scaledPatch, scaledPatch);
            for (int filterIndex = 0; filterIndex < FILTER_COUNT; ++filterIndex) {
                descriptors.at<double>(patchIndex, scale * FILTER_COUNT + filterIndex) =
                    meanAbsolute(responses[filterIndex](region));
            }
        }
    }
    return {descriptors, patches};
}

cv::Mat standardize(const cv::Mat& values) {
    cv::Mat standardized = values.clone();
    for (int column = 0; column < values.cols; ++column) {
        cv::Scalar mean, stddev;
        cv::meanStdDev(values.col(column), mean, stddev);
        const double scale = stddev[0] > 1e-12 ? stddev[0] : 1.0;
        for (int row = 0; row < values.rows; ++row) {
            standardized.at<double>(row, column) = (values.at<double>(row, column) - mean[0]) / scale;
        }
    }
    return standardized;
}

void writeNpy(const fs::path& path, const cv::Mat& values) {
    std::ofstream file(path, std::ios::binary);
    const std::string header = "{'descr': '<f8', 'fortran_order': False, 'shape': (" +
        std::to_string(values.rows) + ", " + std::to_string(values.cols) + "), }";
    const int padding = 16 - ((10 + header.size() + 1) % 16);
    const std::string padded = header + std::string(padding, ' ') + "\n";
    file.write("\x93NUMPY", 6);
    file.put(1); file.put(0);
    const uint16_t headerSize = static_cast<uint16_t>(padded.size());
    file.write(reinterpret_cast<const char*>(&headerSize), sizeof(headerSize));
    file.write(padded.data(), static_cast<std::streamsize>(padded.size()));
    for (int row = 0; row < values.rows; ++row) {
        file.write(reinterpret_cast<const char*>(values.ptr<double>(row)),
                   static_cast<std::streamsize>(values.cols * sizeof(double)));
    }
}

void writeCsv(const fs::path& path, const DescriptorData& data, const cv::Mat& labels) {
    static const std::vector<std::string> filters = {
        "horizontal", "vertical", "45_graus", "135_graus", "laplaciano", "log", "difusao", "circular"
    };
    std::ofstream file(path);
    file << "recorte,linha,coluna";
    for (int scale = 1; scale <= SCALE_COUNT; ++scale) {
        for (const auto& filter : filters) file << ",escala" << scale << "_" << filter;
    }
    file << ",grupo\n" << std::fixed << std::setprecision(8);
    for (int row = 0; row < data.values.rows; ++row) {
        file << row << "," << data.patches[row].row << "," << data.patches[row].column;
        for (int column = 0; column < data.values.cols; ++column) file << "," << data.values.at<double>(row, column);
        file << "," << labels.at<int>(row, 0) + 1 << "\n";
    }
}

cv::Scalar colorFor(int label) {
    static const cv::Scalar colors[] = {
        {57, 70, 230}, {138, 123, 29}, {97, 162, 244}, {143, 157, 42}, {144, 117, 87}
    };
    return colors[label % 5];
}

void saveResults(const fs::path& output, const cv::Mat& image, const DescriptorData& data, const cv::Mat& labels) {
    cv::Mat overlay;
    cv::cvtColor(image, overlay, cv::COLOR_GRAY2BGR);
    const int columns = 8;
    const int tileSize = 180;
    const int rows = static_cast<int>(std::ceil(data.patches.size() / static_cast<double>(columns)));
    cv::Mat montage(rows * tileSize, columns * tileSize, CV_8UC3, cv::Scalar(30, 30, 30));
    for (int index = 0; index < static_cast<int>(data.patches.size()); ++index) {
        const auto& patch = data.patches[index];
        const cv::Scalar color = colorFor(labels.at<int>(index, 0));
        cv::rectangle(overlay, cv::Rect(patch.column, patch.row, PATCH_SIZE, PATCH_SIZE), color, 8);
        cv::putText(overlay, std::to_string(labels.at<int>(index, 0) + 1),
                    cv::Point(patch.column + 15, patch.row + 42), cv::FONT_HERSHEY_SIMPLEX, 1.2, color, 3);
        cv::Mat tile;
        cv::resize(patch.image, tile, cv::Size(tileSize, tileSize));
        cv::cvtColor(tile, tile, cv::COLOR_GRAY2BGR);
        cv::putText(tile, "recorte " + std::to_string(index), cv::Point(7, 22), cv::FONT_HERSHEY_SIMPLEX, 0.45, color, 1);
        cv::putText(tile, "grupo " + std::to_string(labels.at<int>(index, 0) + 1), cv::Point(7, 43), cv::FONT_HERSHEY_SIMPLEX, 0.45, color, 1);
        tile.copyTo(montage(cv::Rect((index % columns) * tileSize, (index / columns) * tileSize, tileSize, tileSize)));
    }
    cv::imwrite((output / "categorizacao_imagem.jpg").string(), overlay, {cv::IMWRITE_JPEG_QUALITY, 90});
    cv::imwrite((output / "categorizacao_recortes.jpg").string(), montage, {cv::IMWRITE_JPEG_QUALITY, 92});
}

int main(int argc, char** argv) {
    try {
        const fs::path imagePath = argc > 1 ? argv[1] : "image.jpg";
        const fs::path output = argc > 2 ? argv[2] : "resultados_cpp";
        const int patchCount = argc > 3 ? std::stoi(argv[3]) : 32;
        const int groups = argc > 4 ? std::stoi(argv[4]) : 4;
        fs::create_directories(output);

        cv::Mat input = cv::imread(imagePath.string(), cv::IMREAD_GRAYSCALE);
        if (input.empty()) throw std::runtime_error("Nao foi possivel abrir " + imagePath.string());
        if (input.cols < PATCH_SIZE || input.rows < PATCH_SIZE) throw std::runtime_error("A imagem deve ter pelo menos 512x512 pixels.");

        const DescriptorData data = extractDescriptors(input, patchCount);
        if (data.values.rows < groups) throw std::runtime_error("Numero de recortes menor que o numero de grupos.");
        const cv::Mat standardizedDouble = standardize(data.values);
        cv::Mat standardized;
        standardizedDouble.convertTo(standardized, CV_32F);
        cv::Mat labels, centers;
        const double compactness = cv::kmeans(standardized, groups, labels,
            cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER, 100, 1e-5),
            20, cv::KMEANS_PP_CENTERS, centers);

        writeCsv(output / "descritores_24d.csv", data, labels);
        writeNpy(output / "descritores_24d.npy", data.values);
        saveResults(output, input, data, labels);
        std::cout << "Imagem: " << input.cols << "x" << input.rows << " pixels, tons de cinza\n"
                  << "Recortes analisados: " << data.values.rows << " de 512x512\n"
                  << "Descritores: " << data.values.rows << "x" << data.values.cols << " (8 filtros x 3 escalas)\n"
                  << "Agrupamento: K-Means, " << groups << " grupos, distancia euclidiana padronizada\n"
                  << "Compactacao final: " << compactness << "\n"
                  << "Resultados: " << fs::absolute(output) << "\n";
    } catch (const std::exception& error) {
        std::cerr << "Erro: " << error.what() << "\n";
        return 1;
    }
    return 0;
}