//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SessionEngine.mqh                                      |
//| Layer   : Brain / Session / Engines                              |
//| Version : 2.0.0                                                  |
//| Purpose : Trading Session state and progress analysis            |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SESSION_ENGINES_SESSIONENGINE_MQH
#define CORE_BRAIN_SESSION_ENGINES_SESSIONENGINE_MQH

#include "../config/SessionConfig.mqh"
#include "../models/SessionContext.mqh"
#include "../models/SessionResult.mqh"

//--------------------------------------------------
// Session Engine
//--------------------------------------------------

class CSessionEngine
{
private:
    CSessionConfig m_config;

public:
    //--------------------------------------------------

    void SetConfig(const CSessionConfig &config)
    {
        m_config = config;
    }

    //--------------------------------------------------

    CSessionResult Analyze(const CSessionContext &context)
    {
        CSessionResult result;

        result.Reset();

        MqlDateTime tm;

        TimeToStruct(context.CurrentTime, tm);

        //--------------------------------------------------
        // Phase 1
        // Trading Session Detection
        //--------------------------------------------------

        if (tm.hour >= 0 && tm.hour < 8)
        {
            result.State = SESSION_ASIA;

            result.Tradable = m_config.EnableAsia;
        }
        else if (tm.hour >= 8 && tm.hour < 16)
        {
            result.State = SESSION_LONDON;

            result.Tradable = m_config.EnableLondon;
        }
        else
        {
            result.State = SESSION_NEWYORK;

            result.Tradable = m_config.EnableNewYork;
        }

        const int session_start_hour = (tm.hour / 8) * 8;
        const int elapsed_minutes = ((tm.hour - session_start_hour) * 60) + tm.min;
        result.Progress = MathMax(0.0, MathMin(100.0,
           100.0 * elapsed_minutes / 480.0));

        result.Confidence = 1.0;

        return result;
    }
};

#endif
