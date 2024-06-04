#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cmath>
#include "graph.h"
#include <cmath>
#include <limits.h>
#include <map>
#define V 7698

using namespace std;
//using namespace waikiki;


int adjMatrixHelper(vector<int> v, int value) {
    for (int i = 0; i < v.size(); i++) {
        if (v[i] == value) {
            return i;
        }
    }
    return -1;
}

double calculateDis(double sourcelat, double sourcelng, double deslat, double deslng) {
    // great circle formula
    return 3963.0 * acos((sin(sourcelat) * sin(deslat)) + cos(sourcelat) * cos(deslat) * cos(deslng - deslat));
}

int minDistance(int dist[], bool visited[]){
   
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
void printSolution(vector<int> airportID, int dist[], map<int,int> path, int dest, int src){

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


void dijkstra(vector<vector<double> > adjMatrix, vector<int> airportID, int src, int dest){

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

int main()
{
     std::cout <<  "line 28" << std::endl;
    /**
    * parameters setup
    **/
    // used for data parsing

    vector<int> airportID;
    vector<double> airportlat;
    vector<double> airportlng;
    vector<int> sourceID;
    vector<int> destinationID;
    // used for adjacency matrix
    
    vector<vector<double> > adjMatrix;
    /**
     * data parsing
    **/

    std::string line;
    //data parse for airportID file
    std::ifstream airportFile("airports.dat");
    
    //if not open throw an exception
    /*if(!airportFile.is_open()) {
        throw graph_excepts::airport_parse_error("File not opened");
    }*/
    string id, name, city, country, iata, icao, lat, lng;

    while(std::getline(airportFile, line)) {
        stringstream ss(line);
        getline(ss, id, ',');
        getline(ss, name, ',');
        getline(ss, city, ',');
        getline(ss, country, ',');
        getline(ss, iata, ',');
        getline(ss, icao, ',');
        getline(ss, lat, ',');
        getline(ss, lng, ',');

        std::stringstream ID(id);
        int idvec;
        ID >> idvec;
        airportID.push_back(idvec); // airport ID stored
        std::stringstream la(lat);
        double latvec;
        la >> latvec;
        airportlat.push_back(latvec); // airport latitude stored
        std::stringstream lo(lng);
        double lngvec;
        lo >> lngvec;
        airportlng.push_back(lngvec); // airport longitude stored
    }

    //data parse for route file
    std::ifstream routesFile("routes.dat");
    // if not open throw an exception
    /*if (!routesFile.is_open()) {
        throw graph_excepts::airport_parse_error("File not opened");
    }*/

    string airline, airlineid, sairport, source, dairport, destination;

    while (std::getline(routesFile, line)) {
        stringstream ss(line);
        getline(ss, airline, ',');
        getline(ss, airlineid, ',');
        getline(ss, sairport, ',');
        getline(ss, source, ',');
        getline(ss, dairport, ',');
        getline(ss, destination, ',');

        std::stringstream sid(source);
        int sID;
        sid >> sID;
        sourceID.push_back(sID); // source ID stored
        std::stringstream did(destination);
        int dID;
        did >> dID;
        destinationID.push_back(dID); // destination ID stored
    }

    // test for data parsing
    /*for (int i = 0; i < sourceID.size(); i++) {
        std::cout << sourceID[i] << std::endl;
    }
    std::cout << airportID.size() << std::endl;
    std::cout << airportlat.size() << std::endl;
    std::cout << airportlng.size() << std::endl;
    std::cout << sourceID.size() << std::endl;
    std::cout << destinationID.size()<< std::endl;*/

    /**
     * building adjacency matrix
     **/
    // test case for matrix functions
    /*vector<int> adj = {1,2,3,4,5,6};
    int a = adjMatrixHelper(adj, 2);
    cout << a << endl; */

    // create empty matrix
    adjMatrix.resize(airportID.size());
    for (unsigned int i = 0; i < adjMatrix.size(); i++) {
        adjMatrix[i].resize(airportID.size());

    }

    // import routes data
    for (unsigned int j = 0; j < adjMatrix.size(); j++) {
        int sourceIndex = adjMatrixHelper(airportID, sourceID[j]);
        int destinationIndex = adjMatrixHelper(airportID, destinationID[j]);
        if (sourceIndex == -1 || destinationIndex == -1) {
            continue;
        }

        double dist=calculateDis(airportlat[sourceIndex], airportlng[sourceIndex], airportlat[destinationIndex], airportlng[destinationIndex]);
        adjMatrix[sourceIndex][destinationIndex] = dist;
        adjMatrix[destinationIndex][sourceIndex]= dist;

        // weighted edges using great circle
    }

    dijkstra(adjMatrix, airportID, 2965, 2990);

    return 0; 
}

