//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SessionContext.mqh                                     |
//| Layer   : Brain / Session / Models                               |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SESSION_MODELS_SESSIONCONTEXT_MQH
#define CORE_BRAIN_SESSION_MODELS_SESSIONCONTEXT_MQH

class CSessionContext
{
public:
    string Symbol;

    ENUM_TIMEFRAMES Timeframe;

    datetime CurrentTime;

    CSessionContext()
    {
        Symbol = "";

        Timeframe = PERIOD_CURRENT;

        CurrentTime = 0;
    }
};

#endif