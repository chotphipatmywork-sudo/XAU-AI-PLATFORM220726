//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowRiskGate.mq5                                 |
//| Layer   : Tests / Risk / Shadow                                  |
//| Version : 1.0.0                                                  |
//| Purpose : Verify explicit paper-risk and live-lock protections   |
//+------------------------------------------------------------------+

#property strict

#include "../core/risk/RiskManager.mqh"
#include "../core/execution/models/ExecutionModeConfig.mqh"

bool Check(const bool condition,const string message)
  {
   if(!condition)
      Print("Shadow Risk test failed: ",message);
   return(condition);
  }

CDecisionResult BuyIntent()
  {
   CDecisionResult decision;
   decision.Decision=DECISION_BUY;
   decision.Confidence=75.0;
   decision.Valid=true;
   return(decision);
  }

int OnInit()
  {
   CExecutionModeConfig mode;
   const bool modeValid=(mode.IsShadow() &&
                         mode.IsLiveLocked() &&
                         !mode.ModelDeploymentAuthorized &&
                         !mode.LiveExecutionAuthorized);

   CRiskManager risk;
   risk.SetShadowLossLimits(100.0,150.0);
   const CDecisionResult decision=BuyIntent();

   CShadowRiskContext clear;
   const CRiskResult approved=risk.Evaluate(decision,clear);

   CShadowRiskContext exposure;
   exposure.PaperPositionActive=true;
   const CRiskResult exposureBlocked=risk.Evaluate(decision,exposure);

   CShadowRiskContext stale;
   stale.MarketStale=true;
   const CRiskResult staleBlocked=risk.Evaluate(decision,stale);

   CShadowRiskContext dailyLoss;
   dailyLoss.DailyProfitPoints=-100.0;
   const CRiskResult dailyLossBlocked=risk.Evaluate(decision,dailyLoss);

   CShadowRiskContext drawdown;
   drawdown.DrawdownPoints=150.0;
   const CRiskResult drawdownBlocked=risk.Evaluate(decision,drawdown);

   risk.SetEmergencyStop(true);
   const CRiskResult emergencyBlocked=risk.Evaluate(decision,clear);

   const bool valid=
      Check(modeValid,"safe-default execution mode") &&
      Check(approved.Valid && approved.AllowTrade,"clear Shadow context") &&
      Check(!exposureBlocked.AllowTrade,"one-position exposure") &&
      Check(!staleBlocked.AllowTrade,"stale market") &&
      Check(!dailyLossBlocked.AllowTrade,"daily loss") &&
      Check(!drawdownBlocked.AllowTrade,"drawdown") &&
      Check(!emergencyBlocked.AllowTrade &&
            emergencyBlocked.EmergencyStop,"emergency stop");

   Print("Shadow execution mode lock valid: ",modeValid);
   Print("Shadow clear Risk approval valid: ",approved.AllowTrade);
   Print("Shadow active exposure blocked: ",!exposureBlocked.AllowTrade);
   Print("Shadow stale market blocked: ",!staleBlocked.AllowTrade);
   Print("Shadow daily loss blocked: ",!dailyLossBlocked.AllowTrade);
   Print("Shadow drawdown blocked: ",!drawdownBlocked.AllowTrade);
   Print("Shadow emergency stop blocked: ",!emergencyBlocked.AllowTrade);
   Print("Shadow Risk gate valid: ",valid);
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
