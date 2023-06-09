module RealEstate {
    exception GenericError { 
        string reason; 
    }; 
    interface RealEstateInterface {
        string getZoneData();
        string getPropertyData();
    };
};