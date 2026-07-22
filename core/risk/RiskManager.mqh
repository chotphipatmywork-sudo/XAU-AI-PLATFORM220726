//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : RiskManager.mqh                                        |
//| Layer   : Core / Risk                                            |
//| Version : 4.0.0                                                  |
//| Purpose : Central Risk Manager                                   |
//+------------------------------------------------------------------+

#ifndef CORE_RISK_RISKMANAGER_MQH
#define CORE_RISK_RISKMANAGER_MQH

#include "RiskEngine.mqh"
#include "models/RiskSnapshot.mqh"
#include "models/RiskResult.mqh"
#include "../decision/models/DecisionResult.mqh"
#include "models/ShadowRiskContext.mqh"

class CRiskManager
{
private:

   CRiskEngine m_engine;

   double m_riskPercent;

   double m_maxShadowDailyLossPoints;

   double m_maxShadowDrawdownPoints;

public:

   CRiskManager()
   {
      m_riskPercent = 1.0;
      m_maxShadowDailyLossPoints = 2000.0;
      m_maxShadowDrawdownPoints = 3000.0;
   }

   void SetRiskPercent(const double percent)
   {
      if(percent > 0.0)
         m_riskPercent = percent;
   }

   double GetRiskPercent() const
   {
      return m_riskPercent;
   }

   CRiskResult Evaluate()
   {
      return m_engine.Evaluate();
   }

   CRiskResult Evaluate(const CDecisionResult &decision)
   {
      CRiskResult result;
      if(!decision.Valid)
      {
         result.Reject("Risk rejected an invalid Decision.");
         return result;
      }
      if(decision.Decision != DECISION_BUY &&
         decision.Decision != DECISION_SELL)
      {
         result.Reject("Risk rejected a non-actionable Decision.");
         return result;
      }
      result=m_engine.Evaluate();
      if(result.AllowTrade)
         result.RecommendedRisk=m_riskPercent;
      return result;
   }

   CRiskResult Evaluate(const CDecisionResult &decision,
                        const CShadowRiskContext &shadow)
   {
      CRiskResult result=Evaluate(decision);
      if(!result.AllowTrade)
         return result;
      if(shadow.MarketStale)
      {
         result.Reject("Risk blocked stale market data.");
         return result;
      }
      if(shadow.PaperPositionActive)
      {
         result.Reject("Risk blocked additional Shadow exposure.");
         return result;
      }
      if(shadow.DailyProfitPoints<=-m_maxShadowDailyLossPoints)
      {
         result.Reject("Risk blocked the Shadow daily loss limit.");
         return result;
      }
      if(shadow.DrawdownPoints>=m_maxShadowDrawdownPoints)
      {
         result.Reject("Risk blocked the Shadow drawdown limit.");
         return result;
      }
      return result;
   }

   void SetShadowLossLimits(const double dailyLossPoints,
                            const double drawdownPoints)
   {
      if(dailyLossPoints>0.0)
         m_maxShadowDailyLossPoints=dailyLossPoints;
      if(drawdownPoints>0.0)
         m_maxShadowDrawdownPoints=drawdownPoints;
   }

   void SetMaxDailyLossPercent(const double percent)
   {
      m_engine.SetMaxDailyLossPercent(percent);
   }

   void SetEmergencyStop(const bool enabled)
   {
      m_engine.SetEmergencyStop(enabled);
   }

   bool EmergencyStopEnabled() const
   {
      return m_engine.EmergencyStopEnabled();
   }

   bool AllowTrading()
   {
      return m_engine.AllowTrading();
   }

   CRiskSnapshot GetSnapshot()
   {
      CRiskSnapshot snapshot;

      snapshot.Reset();

      snapshot.Balance =
         AccountInfoDouble(ACCOUNT_BALANCE);

      snapshot.Equity =
         AccountInfoDouble(ACCOUNT_EQUITY);

      snapshot.DrawdownPercent =
         m_engine.DrawdownPercent();

      snapshot.DailyLossPercent =
         m_engine.DailyLossPercent();

      snapshot.RiskPercent =
         m_riskPercent;

      snapshot.TradingAllowed =
         m_engine.AllowTrading();

      return snapshot;
   }

};

#endif
