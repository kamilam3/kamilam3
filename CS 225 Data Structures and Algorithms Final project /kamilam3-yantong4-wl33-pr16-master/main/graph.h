# pragma once

# include <vector>
# include <map>

using namespace std;

/**
 * The Graph class is used to build the graph matrix.
**/
class Graph {
    public:
        //Graph(vector<vector<double>> &adjMatrix, vector<int> airportID, vector<int> sourceID, vector<int> destinationID, vector<double> airportlat, vector<double> airportlng);
        Graph(vector<int> airportID, vector<int> sourceID, vector<int> destinationID, vector<double> airportlat, vector<double> airportlng);
        void dijkstra(vector<int> airportID, int src, int dest);
        //void insertVertex();
        /*void insertEdge(int vertex1, int vertex2);
        void removeVertex( int vertex1);
        void removeEdge( int vertex1, int vertex2 );
        bool areAdjcent(int vertex1, int vertex2);
        vector <int> incidentEdges(int vertex1);*/

    private:
        int adjMatrixHelper(vector<int> v, int value);
        double calculateDis(double sourcelat, double sourcelng, double deslat, double deslng);
        vector<vector<double> > adjMatrix;
        int minDistance(int dist[], bool visited[]);
        void printSolution(vector<int> airportID, int dist[], map<int,int> path, int dest, int src);

};

