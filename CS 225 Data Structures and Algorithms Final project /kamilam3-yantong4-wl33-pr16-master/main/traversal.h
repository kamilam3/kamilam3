#pragma once

# include <vector>
# include <queue>

using namespace std;

/**
 * This class is used to perform BFS traversal of the adjacency matrix we have build from openflights datasets.
 * **/
class traversal {
    public:
        traversal(); // simple constructor
        traversal(const vector<vector<double>> matrix); // copy constructor to make a copy of the matrix build in main.cpp
        void bfs(int source);
        void printBFS();

    private:
        vector<int> start;
        vector<bool> isVisited;
        vector<vector<double>> adjMatrix;
        vector<int> bfsPrint;

};