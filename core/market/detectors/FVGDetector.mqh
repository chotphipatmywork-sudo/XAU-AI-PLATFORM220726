//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : FVGDetector.mqh                                        |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_FVGDETECTOR_MQH
#define CORE_MARKET_DETECTORS_FVGDETECTOR_MQH

#include "../models/PriceSeries.mqh"


enum ENUM_FVG_TYPE
{
    FVG_NONE = 0,
    FVG_BULLISH,
    FVG_BEARISH
};


class CFVGState
{

public:

    ENUM_FVG_TYPE Type;

    double Upper;

    double Lower;

    datetime Time;

    bool Valid;


    CFVGState()
    {
        Reset();
    }


    void Reset()
    {
        Type = FVG_NONE;

        Upper = 0.0;
        Lower = 0.0;

        Time = 0;

        Valid = false;
    }

};



class CFVGDetector
{

public:

    CFVGState Detect(
        const CPriceSeriesModel &series)
    {
        CFVGState state;

        return state;
    }

};


#endif