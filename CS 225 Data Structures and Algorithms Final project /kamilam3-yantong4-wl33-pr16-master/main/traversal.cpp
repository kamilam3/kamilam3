# include "traversal.h"
# include "graph.h"
# include <vector>
# include <iostream>

using namespace std;

traversal::traversal() {}

traversal::traversal(const vector<vector<double>> matrix) {
    adjMatrix.resize(matrix.size());
    for(unsigned int i = 0; i < adjMatrix.size(); i++) {
        adjMatrix[i].resize(matrix.size());
    }
    
    for(unsigned int j = 0; j < adjMatrix.size(); j++) {
        for (unsigned int k = 0; k <adjMatrix[j].size(); k++) {
            adjMatrix[j][k] = matrix[j][k];
        }
    }

    isVisited.resize(matrix.size(), false);
}

void traversal::bfs(int source) {
    // store the source into the visited matrix and set as visited
    start.push_back(source);
    isVisited[source] = true;
    int visit;
    while (!start.empty()) {
        visit = start[0];
        bfsPrint.push_back(visit);
        start.erase(start.begin());
        for (unsigned int i = 0; i < adjMatrix[visit].size(); i++) {
            if (adjMatrix[visit][i] == 1 && (!isVisited[i])) {
                // Push the adjacent node to the queue
                start.push_back(i);
                // Set
                isVisited[i] = true;
            }
        }
    }
}

void traversal::printBFS() {
    for(unsigned int i  = 0; i < bfsPrint.size(); i++) {
        std::cout << bfsPrint[i] << std::endl;
    }
}
