#pragma once

#include<string>
#include <fstream>
#include <istream>
#include <iostream>
#include <vector>

using namespace std;

class File {
    public:
      void storeAirports( );
      void storeRoutes( );
      vector<int> get_airportID();
      vector<int> get_destinationID();
      vector<int> get_sourceID();
      vector<double> get_airportlat();
      vector<double> get_airportlng();
      vector<string> get_arport_IATA();

    private: 
    vector<int> airportID;
    vector<double> airportlat;
    vector<double> airportlng;
    vector<int> sourceID;
    vector<int> destinationID;
    vector<string> arport_IATA;
   
  };




/*vector<string> getIATA();
vector<string> get_arr_IATA();
vector<string> get_depart_IATA();
vector<double> get_latitude();
vector<double> get_longitude();
File();
void read_file();


private:
vector<string> IATA_;
vector<string> arr_IATA_;
vector<string> depart_IATA_;

vector<double> latitude_;
vector<double> longitude_;*/


