//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : Context.mqh                                            |
//| Layer   : Brain                                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Shared market context for Brain                        |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_CONTEXT_MQH
#define CORE_BRAIN_CONTEXT_MQH

class CContext
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;

public:
    CContext()
    {
        m_symbol = "";
        m_timeframe = PERIOD_CURRENT;
    }

    void SetSymbol(const string symbol)
    {
        m_symbol = symbol;
    }

    string Symbol() const
    {
        return m_symbol;
    }

    void SetTimeframe(const ENUM_TIMEFRAMES timeframe)
    {
        m_timeframe = timeframe;
    }

    ENUM_TIMEFRAMES Timeframe() const
    {
        return m_timeframe;
    }
};

#endif