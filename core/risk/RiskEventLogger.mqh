//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskEventLogger.mqh                                    |
//| Layer   : Risk                                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Risk Event Logging                                     |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKEVENTLOGGER_MQH
#define CORE_RISK_RISKEVENTLOGGER_MQH

enum ENUM_RISK_EVENT
{
    RISK_EVENT_NONE = 0,
    RISK_EVENT_DRAWDOWN_LIMIT,
    RISK_EVENT_DAILY_LOSS_LIMIT,
    RISK_EVENT_EXPOSURE_LIMIT,
    RISK_EVENT_TRADE_BLOCKED
};

class CRiskEventLogger
{
private:
    ENUM_RISK_EVENT m_lastEvent;

    string m_message;

public:
    CRiskEventLogger()
    {
        Reset();
    }

    void Reset()
    {
        m_lastEvent = RISK_EVENT_NONE;

        m_message = "";
    }

    void Log(
        ENUM_RISK_EVENT event,
        string message)
    {
        m_lastEvent = event;

        m_message = message;
    }

    ENUM_RISK_EVENT LastEvent() const
    {
        return m_lastEvent;
    }

    string Message() const
    {
        return m_message;
    }

    bool HasEvent() const
    {
        return m_lastEvent != RISK_EVENT_NONE;
    }
};

#endif