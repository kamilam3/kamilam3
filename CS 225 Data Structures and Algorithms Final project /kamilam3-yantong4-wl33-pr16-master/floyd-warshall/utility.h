#pragma once


#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <limits>

using namespace std;
using std::string;

namespace waikiki {

    constexpr int mat_t = 15000; //default matrix size
    constexpr double NO_EDGE = -1; //empty matrix value
    constexpr double R_EARTH = 6371.0;
    constexpr double loadFactor = 0.25; // what % of vertices does this vertex connect to
    constexpr double INF = std::numeric_limits<double>::infinity();


namespace graph_excepts {
        class route_parse_error : public std::exception {
        public:
            route_parse_error(string error) : error_{error} {}
            const char* what() const noexcept override {
                return error_.c_str();
            }
        private:
            string error_; //error message
        };

        class airport_parse_error : public std::exception {
        public:
            airport_parse_error(string error) : error_{error} {}
            const char* what () const noexcept override {
                return error_.c_str();
            }
        private:
            string error_;
        };

    } //namespace errorhandling


}
