//+------------------------------------------------------------------+

#ifndef CORE_MARKET_SWINGPOINT_MQH
#define CORE_MARKET_SWINGPOINT_MQH

class CSwingPoint
{
public:
    datetime Time;

    double Price;

    bool High;

    void Reset()
    {
        Time = 0;
        Price = 0;
        High = false;
    }
};

#endif