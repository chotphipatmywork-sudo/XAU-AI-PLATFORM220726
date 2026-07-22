//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SessionResult.mqh                                      |
//| Layer   : Brain / Session / Models                               |
//| Version : 2.0.0                                                  |
//| Purpose : Session state and intra-session market context         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SESSION_MODELS_SESSIONRESULT_MQH
#define CORE_BRAIN_SESSION_MODELS_SESSIONRESULT_MQH

enum ENUM_SESSION_STATE
{
    SESSION_UNKNOWN = 0,

    SESSION_ASIA,

    SESSION_LONDON,

    SESSION_NEWYORK
};

class CSessionResult
{
public:
    ENUM_SESSION_STATE State;

    bool Tradable;

    double Confidence;

    double Progress;

    CSessionResult()
    {
        Reset();
    }

    void Reset()
    {
        State = SESSION_UNKNOWN;

        Tradable = false;

        Confidence = 0.0;

        Progress = 0.0;
    }
};

#endif
