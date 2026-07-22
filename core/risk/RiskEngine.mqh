//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskEngine.mqh                                         |
//| Layer   : Core / Risk                                            |
//| Version : 1.2.0                                                  |
//| Purpose : Risk Evaluation Engine                                 |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKENGINE_MQH
#define CORE_RISK_RISKENGINE_MQH

#include "RiskAnalyzer.mqh"
#include "models/RiskResult.mqh"


class CRiskEngine
{
private:

   CRiskAnalyzer m_analyzer;


public:


   CRiskEngine()
   {
   }



   CRiskResult Evaluate()
   {

      CRiskResult result;


      result.Reset();



      if(m_analyzer.AllowTrading())
      {

         result.Accept(
            "Risk evaluation passed.");

         result.Level = RISK_SAFE;

         result.Score = 100.0;

         result.RecommendedRisk = 1.0;

      }
      else
      {

         result.Reject(
            "Risk evaluation blocked.");

         result.Level = RISK_BLOCK;

         result.Score = 0.0;

         result.RecommendedRisk = 0.0;

         result.EmergencyStop =
            m_analyzer.EmergencyStopEnabled();

      }


      return result;

   }

   void SetMaxDailyLossPercent(const double percent)
   {
      m_analyzer.SetMaxDailyLossPercent(percent);
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_analyzer.SetEmergencyStop(enabled);
   }

   bool EmergencyStopEnabled() const
   {
      return m_analyzer.EmergencyStopEnabled();
   }



   bool AllowTrading()
   {
      return m_analyzer.AllowTrading();
   }



   double DrawdownPercent()
   {
      return m_analyzer.DrawdownPercent();
   }



   double DailyLossPercent()
   {
      return m_analyzer.DailyLossPercent();
   }



   double EquityPercent()
   {
      return m_analyzer.EquityPercent();
   }

};


#endif
