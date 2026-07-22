//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : OrderBlockDetector.mqh                                 |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_ORDERBLOCKDETECTOR_MQH
#define CORE_MARKET_DETECTORS_ORDERBLOCKDETECTOR_MQH

#include "../models/PriceSeries.mqh"

enum ENUM_ORDERBLOCK_TYPE
{
    ORDERBLOCK_NONE = 0,
    ORDERBLOCK_BULLISH,
    ORDERBLOCK_BEARISH
};

class COrderBlockState
{
public:

    ENUM_ORDERBLOCK_TYPE Type;

    double High;

    double Low;

    datetime Time;

    bool Valid;

    COrderBlockState()
    {
        Reset();
    }

    void Reset()
    {
        Type = ORDERBLOCK_NONE;
        High = 0.0;
        Low = 0.0;
        Time = 0;
        Valid = false;
    }
};

class COrderBlockDetector
{
public:

    COrderBlockState Detect(const CPriceSeriesModel &series)
    {
        COrderBlockState state;

        return state;
    }
};

#endif