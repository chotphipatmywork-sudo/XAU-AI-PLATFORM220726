//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PortfolioContext.mqh                                   |
//| Layer   : Core / Portfolio / Models                              |
//| Version : 1.0.0                                                  |
//| Purpose : Portfolio Context                                      |
//+------------------------------------------------------------------+

#ifndef CORE_PORTFOLIO_MODELS_PORTFOLIOCONTEXT_MQH
#define CORE_PORTFOLIO_MODELS_PORTFOLIOCONTEXT_MQH


class CPortfolioContext
{

public:

    string Symbol;

    int MaxPositions;

    int CurrentPositions;

    double TotalExposure;

    double MaxExposure;

    double AccountBalance;

    double AccountEquity;

    double RiskPercent;

    bool AllowNewPosition;


public:


    CPortfolioContext()
    {
        Reset();
    }



    void Reset()
    {

        Symbol = "";

        MaxPositions = 1;

        CurrentPositions = 0;

        TotalExposure = 0.0;

        MaxExposure = 10.0;

        AccountBalance = 0.0;

        AccountEquity = 0.0;

        RiskPercent = 1.0;

        AllowNewPosition = true;

    }

};


#endif