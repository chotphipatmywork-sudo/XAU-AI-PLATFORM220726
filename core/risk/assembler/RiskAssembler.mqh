//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskAssembler.mqh                                      |
//| Layer   : Core / Risk / Assembler                                |
//| Version : 1.1.0                                                  |
//| Purpose : Assemble Risk Analysis Result                          |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_ASSEMBLER_RISKASSEMBLER_MQH
#define CORE_RISK_ASSEMBLER_RISKASSEMBLER_MQH

#include "../models/RiskResult.mqh"
#include "../models/PositionRiskResult.mqh"
#include "../models/PortfolioRiskResult.mqh"


class CRiskAssembler
{
public:


    CRiskResult Assemble(
        const CPositionRiskResult &position,
        const CPortfolioRiskResult &portfolio)
    {

        CRiskResult result;


        result.Reset();



        if(!position.Valid)
        {
            result.Reject(
                "Position risk invalid.");

            return result;
        }



        if(!portfolio.PortfolioSafe)
        {
            result.Reject(
                "Portfolio risk blocked.");

            return result;
        }



        result.Accept(
            "Risk assembly passed.");



        result.Level =
            RISK_SAFE;



        result.Score =
            100.0;



        result.RecommendedRisk =
            1.0;



        return result;
    }

};


#endif