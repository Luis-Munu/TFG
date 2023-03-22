module server {
    interface serverInterface {
        // we need to update the data stored in mongodb with the new data received as pandas dataframe
        // we need to return a boolean to indicate if the update was successful
        void updateDB(string jsonDf);

        // Now we need to send the data stored in mongodb to the client
        // we need to return a pandas dataframe
        string returnDataframe();
    };
};
