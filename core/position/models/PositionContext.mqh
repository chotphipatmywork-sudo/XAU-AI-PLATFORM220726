//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionContext.mqh                                    |
//| Layer   : Core / Position / Models                               |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_MODELS_POSITIONCONTEXT_MQH
#define CORE_POSITION_MODELS_POSITIONCONTEXT_MQH


class CPositionContext
{

public:

    string Symbol;

    ulong Ticket;

    ENUM_POSITION_TYPE Type;

    double Volume;

    double OpenPrice;

    double StopLoss;

    double TakeProfit;

    double CurrentPrice;


public:


    CPositionContext()
    {
        Reset();
    }



    void Reset()
    {

        Symbol = "";

        Ticket = 0;

        Type = POSITION_TYPE_BUY;

        Volume = 0.0;

        OpenPrice = 0.0;

        StopLoss = 0.0;

        TakeProfit = 0.0;

        CurrentPrice = 0.0;

    }

};


#endif