#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cmath>
#include "utility.h"
#include "floyd.h"
#define V 1400
using namespace std;
using namespace waikiki;


void floydWarshall(vector<vector<double>> &adjMatrix){

    std::cout << "inside Graph::floydWarshall" << std::endl;
    double dist[V][V];
    std::cout<< "line 22" << std::endl;
    for (int i = 0; i < V; i++){
        for (int j = 0; j < V; j++){
            dist[i][j] = adjMatrix[i][j];
            //std::cout<< dist[i][j] << std::endl;
        }
    }
    
    std::cout<< "line 30" << std::endl;
    for (int k = 0; k < 5; k++) {
      for (int i = 0; i < 5; i++) {
          for (int j = 0; j < 5; j++) {

               std::cout<< dist[i][j] << std::endl; 
               //std::cout<<(dist[i][k] + dist[k][j])<<std::endl;

              if (dist[i][j] > (dist[i][k] + dist[k][j])
                  && (dist[k][j] != INF
                        && dist[i][k] != INF)){
                    dist[i][j] = dist[i][k] + dist[k][j];
              }
          }
      }
   }
}


int main()
{
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
    vector<vector<double>> adjMatrix;

    /**
     * data parsing
    **/
    std::string line;
    //data parse for airportID file
    std::ifstream airportFile("airports.dat");
    //if not open throw an exception
    if(!airportFile.is_open()) {
        throw graph_excepts::airport_parse_error("File not opened");
    }
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
    if (!routesFile.is_open()) {
        throw graph_excepts::airport_parse_error("File not opened");
    }
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
    for (int i = 0; i < sourceID.size(); i++) {
        std::cout << sourceID[i] << std::endl;
    }

    std::cout << airportID.size() << std::endl;
    std::cout << airportlat.size() << std::endl;
    std::cout << airportlng.size() << std::endl;
    std::cout << sourceID.size() << std::endl;
    std::cout << destinationID.size()<< std::endl;
    /**
     * building adjacency matrix
     **/
    Graph g(adjMatrix, airportID, sourceID, destinationID, airportlat, airportlng); // initialize adjmat with parsed data

    floydWarshall(adjMatrix);   

    // test for adjacency matrix
    int countzero = 0;
    int countother = 0;
    for(int i = 0; i < adjMatrix.size();i++) {
        for(int j = 0; j < adjMatrix[i].size();j++) {
            if(adjMatrix[i][j] == 0) {
                countzero++;
                continue;
            } else {
                countother++;
            }
           // std::cout << adjMatrix[i][j] << std::endl;
        }
    }

    //std::cout << countzero << std::endl;
    //std::cout << countother << std::endl;

    return 0; 
}

