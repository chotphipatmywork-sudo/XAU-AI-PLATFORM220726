//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SwingDetector.mqh                                      |
//| Layer   : Market Detection                                       |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_DETECTORS_SWINGDETECTOR_MQH
#define CORE_MARKET_DETECTORS_SWINGDETECTOR_MQH


#include "../models/SwingPoint.mqh"
#include "../models/PriceSeries.mqh"


class CSwingDetector
{

public:


    bool FindLastSwing(
        CPriceSeriesModel &series,
        CSwingPoint &point
    )
    {

        point.Reset();


        int index = 2;


        // Detect Swing High (ตรวจจับยอดราคา)

        if(
            series.High[index] > series.High[index+1] &&
            series.High[index] > series.High[index-1]
        )
        {

            point.Price = series.High[index];

            point.High = true;

            point.Time = TimeCurrent();

            return true;
        }



        // Detect Swing Low (ตรวจจับฐานราคา)

        if(
            series.Low[index] < series.Low[index+1] &&
            series.Low[index] < series.Low[index-1]
        )
        {

            point.Price = series.Low[index];

            point.High = false;

            point.Time = TimeCurrent();

            return true;
        }



        return false;
    }

};


#endif