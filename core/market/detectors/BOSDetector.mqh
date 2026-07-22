//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BOSDetector.mqh                                        |
//| Layer   : Market / Detectors                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Break Of Structure Detector                            |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_BOSDETECTOR_MQH
#define CORE_MARKET_DETECTORS_BOSDETECTOR_MQH


#include "../models/StructureState.mqh"


//--------------------------------------------------
// BOS Direction
//--------------------------------------------------

enum ENUM_BOS_DIRECTION
{
    BOS_NONE = 0,

    BOS_BULLISH,

    BOS_BEARISH
};


//--------------------------------------------------
// BOS Result
//--------------------------------------------------

class CBOSState
{

public:

    ENUM_BOS_DIRECTION Direction;

    bool Valid;


    CBOSState()
    {
        Reset();
    }


    void Reset()
    {
        Direction = BOS_NONE;

        Valid = false;
    }

};



//--------------------------------------------------
// BOS Detector
//--------------------------------------------------

class CBOSDetector
{

public:


    bool Detect(
        const CStructureState &structure,
        CBOSState &result
    )
    {

        result.Reset();



        //------------------------------------------
        // Bullish BOS
        //------------------------------------------

        if(structure.Trend > 0)
        {
            result.Direction = BOS_BULLISH;

            result.Valid = true;

            return true;
        }



        //------------------------------------------
        // Bearish BOS
        //------------------------------------------

        if(structure.Trend < 0)
        {
            result.Direction = BOS_BEARISH;

            result.Valid = true;

            return true;
        }



        return false;
    }

};


#endif