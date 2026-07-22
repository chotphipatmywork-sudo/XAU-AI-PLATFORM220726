//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureDetector.mqh                                  |
//| Layer   : Market / Detectors                                     |
//| Version : 1.0.0                                                  |
//| Purpose : Detect Market Structure                                |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_STRUCTUREDETECTOR_MQH
#define CORE_MARKET_DETECTORS_STRUCTUREDETECTOR_MQH


#include "../models/SwingPoint.mqh"
#include "../models/StructureState.mqh"


class CStructureDetector
{

public:


    bool Detect(
        CSwingPoint &previousSwing,
        CSwingPoint &currentSwing,
        CStructureState &state
    )
    {

        state.Reset();


        //----------------------------------------
        // Validate
        //----------------------------------------

        if(previousSwing.Price <= 0 ||
           currentSwing.Price <= 0)
        {
            return false;
        }



        //----------------------------------------
        // Higher High
        //----------------------------------------

        if(previousSwing.High &&
           currentSwing.High)
        {

            if(currentSwing.Price > previousSwing.Price)
            {
                state.Trend = 1;

                state.LastHigh = currentSwing.Price;

                state.LastHighTime = currentSwing.Time;

                return true;
            }
        }



        //----------------------------------------
        // Lower Low
        //----------------------------------------

        if(!previousSwing.High &&
           !currentSwing.High)
        {

            if(currentSwing.Price < previousSwing.Price)
            {
                state.Trend = -1;

                state.LastLow = currentSwing.Price;

                state.LastLowTime = currentSwing.Time;

                return true;
            }
        }



        return false;
    }

};


#endif