# include "traversal.h"
# include "graph.h"
# include <vector>
# include <iostream>

using namespace std;


void traversal::bfs(int source, vector<int> airportID, vector<vector<double> > adjMatrix) {
    // store the source into the visited matrix and set as visited
    Graph G;
    int source_index=G.adjMatrixHelper(airportID, source);
    vector<bool> isVisited(airportID.size(), false);
    vector<int> q;

    q.push_back(source_index);
    isVisited[source_index] = true;

    int visit;

    int visit;
    while (!q.empty()) {
        visit = q[0];
        bfsPrint.push_back(visit);
        q.erase(q.begin());
        for (int i = 0; i < adjMatrix[visit].size(); i++) {
            if (adjMatrix[visit][i]!=0 && (!isVisited[i])) {
                // Push the adjacent node to the queue
                q.push_back(i);
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
