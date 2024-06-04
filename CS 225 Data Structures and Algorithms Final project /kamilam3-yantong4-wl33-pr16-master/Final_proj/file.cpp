#include <iostream>
#include <istream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "file.h"
#include "../main/utility.h"
using namespace std;
using namespace waikiki;


vector<int> airportID;
    vector<double> airportlat;
    vector<double> airportlng;
    vector<int> sourceID;
    vector<int> destinationID;
    // used for adjacency matrix


void File::storeAirports( ) {

    std::string line;

    std::ifstream airportFile("airports.dat");
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

        std::stringstream IATA(iata);
        string iata_;
        IATA >> iata_;
        arport_IATA.push_back(iata_); // airport ID stored

        std::stringstream la(lat);
        double latvec;
        la >> latvec;
        airportlat.push_back(latvec); // airport latitude stored

        std::stringstream lo(lng);
        double lngvec;
        lo >> lngvec;
        airportlng.push_back(lngvec); // airport longitude stored
    }
}


void File::storeRoutes( ){

    std::string line;
    std::ifstream routesFile("routes.dat");
    
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
    }

vector<int> File::get_airportID(){
    return airportID;
}

vector<int> File::get_destinationID(){
    return destinationID;
}

vector<int> File::get_sourceID(){
    return sourceID;
}

vector<double> File::get_airportlat(){
    return airportlat;
}

vector<double> File::get_airportlng(){
    return airportlng;
}

 vector<string> File::get_arport_IATA(){
      return arport_IATA;
 }


