//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskController.mqh                                     |
//| Layer   : Core / Risk                                            |
//| Version : 1.1.0                                                  |
//| Purpose : Risk Control Engine                                    |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKCONTROLLER_MQH
#define CORE_RISK_RISKCONTROLLER_MQH

#include "models/RiskResult.mqh"


class CRiskController
{

private:

    double m_maxRiskPercent;

    double m_maxDrawdownPercent;


public:


    CRiskController()
    {
        m_maxRiskPercent = 2.0;

        m_maxDrawdownPercent = 20.0;
    }



    bool Validate(
        double riskPercent)
    {

        if(riskPercent <= 0)
            return false;


        if(riskPercent > m_maxRiskPercent)
            return false;


        return true;
    }



    CRiskResult Check()
    {

        CRiskResult result;


        double balance =
            AccountInfoDouble(
                ACCOUNT_BALANCE);


        double equity =
            AccountInfoDouble(
                ACCOUNT_EQUITY);



        if(balance <= 0)
        {
            result.Reject(
                "Invalid balance.");

            return result;
        }



        double drawdown =
            ((balance - equity) / balance) * 100.0;



        if(drawdown > m_maxDrawdownPercent)
        {
            result.Reject(
                "Maximum drawdown exceeded.");

            return result;
        }



        result.Accept(
            "Risk check passed.");


        result.RecommendedRisk =
            m_maxRiskPercent;


        result.Score =
            100.0 - drawdown;


        return result;
    }



    void SetMaxRisk(
        double percent)
    {
        m_maxRiskPercent = percent;
    }



    void SetMaxDrawdown(
        double percent)
    {
        m_maxDrawdownPercent = percent;
    }

};


#endif