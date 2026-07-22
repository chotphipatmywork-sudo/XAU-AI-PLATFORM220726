//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MoneyResult.mqh                                        |
//| Layer   : Core / Money / Models                                  |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_MODELS_MONEYRESULT_MQH
#define CORE_MONEY_MODELS_MONEYRESULT_MQH

class CMoneyResult
{
public:
    bool Valid;

    double LotSize;

public:
    CMoneyResult()
    {
        Reset();
    }

    void Reset()
    {
        Valid = false;
        LotSize = 0.0;
    }
};

#endif