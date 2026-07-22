//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityDetector.mqh                                  |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_LIQUIDITYDETECTOR_MQH
#define CORE_MARKET_DETECTORS_LIQUIDITYDETECTOR_MQH

#include "../models/SwingPoint.mqh"


enum ENUM_LIQUIDITY_TYPE
{
    LIQUIDITY_NONE = 0,
    LIQUIDITY_BUY,
    LIQUIDITY_SELL
};



class CLiquidityState
{

public:

    ENUM_LIQUIDITY_TYPE Type;

    double Level;

    bool Valid;


    CLiquidityState()
    {
        Reset();
    }


    void Reset()
    {
        Type = LIQUIDITY_NONE;

        Level = 0.0;

        Valid = false;
    }

};



class CLiquidityDetector
{

public:

    CLiquidityState Detect(
        const CSwingPoint &swing)
    {
        CLiquidityState state;


        if(swing.Price <= 0)
            return state;



        if(swing.High)
        {
            state.Type = LIQUIDITY_BUY;

            state.Level = swing.Price;

            state.Valid = true;
        }
        else
        {
            state.Type = LIQUIDITY_SELL;

            state.Level = swing.Price;

            state.Valid = true;
        }


        return state;
    }

};


#endif