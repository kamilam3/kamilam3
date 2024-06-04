
# include "graph.h"
# include <vector>
# include <cmath>
#include <iostream>
#include <limits.h>
#include <map>
#define V 7698


using namespace std;

Graph::Graph(){

}

Graph::Graph(vector<int> airportID, vector<int> sourceID, vector<int> destinationID, vector<double> airportlat, vector<double> airportlng) {
    // create empty matrix
    adjMatrix.resize(airportID.size());
    for (unsigned int i = 0; i < adjMatrix.size(); i++) {
        adjMatrix[i].resize(airportID.size());
    }

    // import airports and routes data
    for (unsigned int j = 0; j < adjMatrix.size(); j++) {
        int sourceIndex = adjMatrixHelper(airportID, sourceID[j]);
        int destinationIndex = adjMatrixHelper(airportID, destinationID[j]);
        if (sourceIndex == -1 || destinationIndex == -1) {
            continue;
        }

        // weighted edges using great circle
        double dist=calculateDis(airportlat[sourceIndex], airportlng[sourceIndex], airportlat[destinationIndex], airportlng[destinationIndex]);
        adjMatrix[sourceIndex][destinationIndex] = dist;
        adjMatrix[destinationIndex][sourceIndex]= dist;
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

int Graph::minDistance(int dist[], bool visited[]){
   
    // Initialize min value
    int min = INT_MAX;
    int min_index;
 
    for (int v = 0; v < V; v++){
           if (visited[v] == false && dist[v] <= min){
                 min = dist[v];
                min_index = v;

           }
    }
    return min_index;
}

// A utility function to print the constructed distance array
void Graph::printSolution(vector<int> airportID, int dist[], map<int,int> path, int dest, int src){

    int dest_index= adjMatrixHelper(airportID, dest);
   
    cout <<"Distance from " <<src<<" to "<<dest<<" = "<<dist[dest_index]<<endl;
    
      // reverse map(from,to)
      
      map <int,int> rev_map;
      int i=dest_index;
      int src_index=adjMatrixHelper(airportID, src);
   
      while(path[i]!=src_index){
          rev_map[path[i]]=i;
          i=path[i];
   }
      rev_map[path[i]]=i;
      
  cout <<"Path from source = " <<src<<" to destination = "<<dest<< endl;
  
  int k=src_index;
  while(k!=dest_index){
      std::cout <<"("<< airportID[k] << ", " << airportID[rev_map[k]] << ") " << "\n";
      k=rev_map[k];
  }   
  
}


void Graph::dijkstra(vector<int> airportID, int src, int dest){

    map <int, int> prevNodes;
    
    int dist[V]; // The output array.  dist[i] will hold the shortest
    // distance from src to i
 
    bool visited[V]; // sptSet[i] will be true if vertex i is included in shortest
    // path tree or shortest distance from src to i is finalized
 
    // Initialize all distances as INFINITE and stpSet[] as false
    for (int i = 0; i < V; i++){
         dist[i] = INT_MAX;
        visited[i] = false;
    }

   int src_index= adjMatrixHelper(airportID, src);

    // Distance of source vertex from itself is always 0
    dist[src_index] = 0;
 
    // Find shortest path for all vertices
    for (int count = 0; count < V - 1; count++) {
        // Pick the minimum distance vertex from the set of vertices not
        // yet processed. u is always equal to src in the first iteration.
        int u = minDistance(dist, visited);
 
        // Mark the picked vertex as processed
        visited[u] = true;
       
        // Update dist value of the adjacent vertices of the picked vertex
        
        for (int v = 0; v < V; v++){
            
            // Update dist[v] only if is not in sptSet, there is an edge from
            // u to v, and total weight of path from src to  v through u is
            // smaller than current value of dist[v]
             
            if (!visited[v] && adjMatrix[u][v] && dist[u] != INT_MAX
                && dist[u] + adjMatrix[u][v] < dist[v]){
                    dist[v] = dist[u] + adjMatrix[u][v];
                    //cout<<"u="<<u<<", "<<"v= "<<v<<endl;
                    prevNodes[v]=u;
                }
        }
    }
 
    // print the constructed distance array
    printSolution(airportID, dist, prevNodes, dest, src);
}
 
vector<vector<double> > Graph::get_adjMatrix( ){
    return adjMatrix;
}


