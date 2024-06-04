#include "floyd.h"
#include <vector>
#include <cmath>
#include <iostream> 
using namespace std;
#define V 6883
#define INF INT_MAX

void Graph::floydWarshall(vector<vector<double>> &adjMatrix){

    std::cout << "inside Graph::floydWarshall" << std::endl;
    int dist[V][V];
    int k;
      
    for (unsigned int i = 0; i < V; i++){
        for (unsigned int j = 0; j < V; j++){
            dist[i][j] = adjMatrix[i][j];
        }
    }
   std::cout << "adjMatrix.size()" << std::endl;
   std::cout << adjMatrix.size() << std::endl;
   for (unsigned int k = 0; k < adjMatrix.size(); k++) {
      for (unsigned int i = 0; i < adjMatrix.size(); i++) {
          for (unsigned j = 0; j < adjMatrix.size(); j++) {
              if (dist[i][j] > (dist[i][k] + dist[k][j])
                  && (dist[k][j] != INF
                        && dist[i][k] != INF)){
                    dist[i][j] = dist[i][k] + dist[k][j];

                   // std::cout<< dist[i][j] << std::endl;
              }
          }
      }
   }

}


Graph::Graph(vector<vector<double>> &adjMatrix, vector<int> airportID, vector<int> sourceID, vector<int> destinationID, vector<double> airportlat, vector<double> airportlng) {
    // create empty matrix
    cout << "inside graph" << endl;
    adjMatrix.resize(airportID.size());
    for (unsigned int i = 0; i < adjMatrix.size(); i++) {
         adjMatrix[i].resize(airportID.size());
    }

    // import airports and routes data
    for(unsigned int j = 0; j < adjMatrix.size(); j++) {
        int sourceIndex = adjMatrixHelper(airportID, sourceID[j]);
        int destinationIndex = adjMatrixHelper(airportID, destinationID[j]);
        if (sourceIndex == -1 || destinationIndex == -1) {
            continue;
        }
        std::cout << "sourceIndex" << std::endl;
        std::cout << sourceIndex << std::endl;

        std::cout << "destinationIndex"  << std::endl;
        std::cout << destinationIndex  << std::endl;
 
        adjMatrix[sourceIndex][destinationIndex] = calculateDis(airportlat[sourceIndex], airportlng[sourceIndex], airportlat[destinationIndex], airportlng[destinationIndex]);
        // weighted edges using great circle
       
        std::cout << adjMatrix[sourceIndex][destinationIndex] << std::endl;
        //std::cout << "stop displaying dis" << std::endl;  
        
    }


}

int Graph::adjMatrixHelper(vector<int> v, int value) {
    // used to initialize an empty matrix
    for (int i = 0; i < v.size(); i++) {
        if (v[i] == value) {
            return i;
        }
    }
    return -1;
}

double Graph::calculateDis(double sourcelat, double sourcelng, double deslat, double deslng) {
    // great circle formula
    return 3963.0 * acos((sin(sourcelat) * sin(deslat)) + cos(sourcelat) * cos(deslat) * cos(deslng - deslat));
}

/*
void Graph::insertVertex(vector<vector<double>> &adjMatrix) {

    // increasing the number of vertices
    matrixSize++;
    adjMatrix.resize(matrixSize);
    for (unsigned int x = 0; x < matrixSize; x++) {
        adjMatrix[x].resize(matrixSize);
    }
 
    // initializing the new elements to 0
    for (unsigned int i = 0; i < adjMatrix.size(); ++i) {
        g[i][n - 1] = 0;
        g[n - 1][i] = 0;
    }
}*/
// NOT DONE YET, DO NOT TOUCH

/*void Graph::insertEdge(int vertex1, int vertex2){
    int x=vertex.find(vertex1)->second;
    int y=vertex.find(vertex2)->second;
    int dist=(latitude[x]-latitude[y])*(latitude[x]-latitude[y])+
        (longitude[x]-longitude[y])*(longitude[x]-longitude[y]);
    int weight=sqrt(dist);
    adj_mat[x][y]=weight;
    adj_mat[y][x]=weight;
}

void Graph::removeVertex( int vertex1){
    vertex.erase(vertex1);

    for(int i=0; i<size; i++){
        adj_mat[vertex.find(vertex1)->second][i]=0;
        adj_mat[i][vertex.find(vertex1)->second]=0;
    }

}

void Graph::removeEdge( int vertex1, int vertex2 ){
    adj_mat[vertex.find(vertex1)->second][vertex.find(vertex2)->second]=0;
    adj_mat[vertex.find(vertex2)->second][vertex.find(vertex1)->second]=0;
}

bool Graph::areAdjcent(int vertex1, int vertex2){
    if(adj_mat[vertex.find(vertex1)->second][vertex.find(vertex2)->second]==0){
        return false;
    }
    return true;
}

vector <int> Graph::incidentEdges(int vertex1){
    vector<int> incid;

    for(int i=0; i<vertex.size(); i++){
        int index=vertex.find(vertex1)->second; 
        //it was int index=map.find(vertex1)->second;
        if(adj_mat[i][index]>0&&i!=index){
            incid.push_back(i);
        }
    }

    return incid;
}*/
