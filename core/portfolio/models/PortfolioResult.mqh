//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioResult.mqh                                    |
//| Layer   : Core / Portfolio / Models                              |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Evaluation Result                            |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_MODELS_PORTFOLIORESULT_MQH
#define CORE_PORTFOLIO_MODELS_PORTFOLIORESULT_MQH

//--------------------------------------------------
// Portfolio Status
//--------------------------------------------------

enum ENUM_PORTFOLIO_STATUS
{
    PORTFOLIO_UNKNOWN = 0,

    PORTFOLIO_ALLOWED,

    PORTFOLIO_LIMIT_REACHED,

    PORTFOLIO_BLOCKED
};

//--------------------------------------------------
// Portfolio Result
//--------------------------------------------------

class CPortfolioResult
{

public:
    bool Valid;

    ENUM_PORTFOLIO_STATUS Status;

    bool AllowNewPosition;

    int CurrentPositions;

    int MaxPositions;

    double TotalExposure;

    double MaxExposure;

    string Message;

public:
    CPortfolioResult()
    {
        Reset();
    }

    void Reset()
    {

        Valid = false;

        Status = PORTFOLIO_UNKNOWN;

        AllowNewPosition = false;

        CurrentPositions = 0;

        MaxPositions = 0;

        TotalExposure = 0.0;

        MaxExposure = 0.0;

        Message = "";
    }
};

#endif