//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PositionResult.mqh                                    |
//| Layer   : Core / Position / Models                               |
//+------------------------------------------------------------------+

#ifndef CORE_POSITION_MODELS_POSITIONRESULT_MQH
#define CORE_POSITION_MODELS_POSITIONRESULT_MQH


enum ENUM_POSITION_STATUS
{
    POSITION_UNKNOWN = 0,
    POSITION_FOUND,
    POSITION_NOT_FOUND,
    POSITION_ERROR
};



class CPositionResult
{

public:

    bool Valid;

    ENUM_POSITION_STATUS Status;

    ulong Ticket;

    string Symbol;

    ENUM_POSITION_TYPE Type;

    double Volume;

    double OpenPrice;

    double CurrentPrice;

    double Profit;



public:


    CPositionResult()
    {
        Reset();
    }



    void Reset()
    {

        Valid = false;

        Status = POSITION_UNKNOWN;

        Ticket = 0;

        Symbol = "";

        Type = POSITION_TYPE_BUY;

        Volume = 0.0;

        OpenPrice = 0.0;

        CurrentPrice = 0.0;

        Profit = 0.0;

    }

};


#endif