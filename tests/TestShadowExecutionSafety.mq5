//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowExecutionSafety.mq5                          |
//| Layer   : Tests / Execution / Shadow                             |
//| Version : 1.1.0                                                  |
//| Purpose : Prove paper execution cannot mutate broker state       |
//+------------------------------------------------------------------+

#property strict

#include "../core/execution/shadow/ShadowExecutionEngine.mqh"

input string ShadowAuditFile="XAU_AI_SHADOW_SAFETY_TEST.csv";
input string ShadowStateFile="XAU_AI_SHADOW_SAFETY_STATE.csv";

bool Check(const bool condition,const string message)
  {
   if(!condition)
      Print("Shadow safety test failed: ",message);
   return(condition);
  }

int OnInit()
  {
   const int positionsBefore=PositionsTotal();
   const int ordersBefore=OrdersTotal();
   FileDelete(ShadowAuditFile);
   FileDelete(ShadowStateFile);

   CShadowExecutionConfig config;
   config.AuditFile=ShadowAuditFile;
   config.StateFile=ShadowStateFile;
   config.DefaultVolume=0.01;
   config.StopLossPoints=100.0;
   config.TakeProfitPoints=200.0;
   config.StateCheckpointSeconds=60;

   CShadowExecutionEngine engine;
   if(!Check(engine.Initialize(config),"initialization"))
      return(INIT_FAILED);

   CExecutionContext context;
   context.Symbol="XAUUSD";
   context.Timeframe=PERIOD_M15;
   context.Ask=2000.20;
   context.Bid=2000.00;
   context.Point=0.01;
   context.CurrentTime=StringToTime("2026.07.16 12:00:00");
   context.Decision.Valid=true;
   context.Decision.Decision=DECISION_BUY;
   context.Decision.Confidence=75.0;

   CRiskResult rejectedRisk;
   rejectedRisk.Reject("Synthetic rejection.");
   CExecutionResult rejected=engine.Execute(context,rejectedRisk);
   if(!Check(!rejected.Success,"rejected Risk opened a paper trade") ||
      !Check(!engine.HasActivePosition(),"rejected Risk changed paper state"))
      return(INIT_FAILED);

   CRiskResult approvedRisk;
   approvedRisk.Accept("Synthetic approval.");
   approvedRisk.Score=100.0;
   approvedRisk.RecommendedRisk=0.25;
   CExecutionResult opened=engine.Execute(context,approvedRisk);
   if(!Check(opened.Success,"approved paper entry") ||
      !Check(opened.Ticket>=900000001,"synthetic ticket range") ||
      !Check(engine.HasActivePosition(),"paper position state"))
      return(INIT_FAILED);

   CShadowExecutionEngine recoveredEngine;
   if(!Check(recoveredEngine.Initialize(config),"paper state recovery initialization") ||
      !Check(recoveredEngine.HasActivePosition(),"active paper state recovery"))
      return(INIT_FAILED);

   CExecutionResult duplicate=recoveredEngine.Execute(context,approvedRisk);
   if(!Check(!duplicate.Success,"duplicate paper entry was accepted"))
      return(INIT_FAILED);

   if(!Check(recoveredEngine.Update(2002.30,2002.50,0.01,
                          StringToTime("2026.07.16 12:15:00")),
             "paper take-profit update") ||
      !Check(!recoveredEngine.HasActivePosition(),"paper take-profit did not close"))
      return(INIT_FAILED);

   recoveredEngine.SetEmergencyStop(true);
   CExecutionResult emergency=recoveredEngine.Execute(context,approvedRisk);
   if(!Check(!emergency.Success,"emergency stop accepted entry"))
      return(INIT_FAILED);

   const bool brokerStateUnchanged=(PositionsTotal()==positionsBefore &&
                                    OrdersTotal()==ordersBefore);
   if(!Check(brokerStateUnchanged,"broker order or position count changed"))
      return(INIT_FAILED);

   Print("Shadow rejected Risk valid: ",!rejected.Success);
   Print("Shadow approved synthetic entry valid: ",opened.Success);
   Print("Shadow duplicate protection valid: ",!duplicate.Success);
   Print("Shadow state recovery valid: ",true);
   Print("Shadow paper lifecycle valid: ",!recoveredEngine.HasActivePosition());
   Print("Shadow emergency stop valid: ",!emergency.Success);
   Print("Shadow broker mutation count unchanged: ",brokerStateUnchanged);
   Print("Shadow execution safety valid: ",brokerStateUnchanged);
   FileDelete(ShadowStateFile);
   ExpertRemove();
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
