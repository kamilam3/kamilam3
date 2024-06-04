#pragma once

# include <vector>
# include <queue>

using namespace std;

/**
 * This class is used to perform BFS traversal of the adjacency matrix we have build from openflights datasets.
 * **/
class traversal {

    public:

        void bfs(int source, vector<int> airportID, vector<vector<double> > adjMatrix);
        void printBFS();

    private:
        vector<int> bfsPrint;

};