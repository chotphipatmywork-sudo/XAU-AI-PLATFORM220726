//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestExecution.mq5                                      |
//| Purpose : Execution Layer Test                                   |
//+------------------------------------------------------------------+
#property strict

#include "../core/execution/Execution.mqh"
#include "../core/brain/Signal.mqh"
#include "../core/brain/Decision.mqh"

//--------------------------------------------------

CExecution Execution;

//--------------------------------------------------

int OnInit()
{
   CSignal signal;

   signal.type = SIGNAL_BUY;
   signal.confidence = 90.0;
   signal.source = "Execution Test";
   signal.reason = "Compile Test";

   CDecision decision;

   decision.SetSignal(signal);

   bool result = Execution.Execute(decision);

   Print("========== EXECUTION ==========");
   Print("Execute Result : ", result);

   return INIT_SUCCEEDED;
}

//--------------------------------------------------

void OnTick()
{
}

//--------------------------------------------------

void OnDeinit(const int reason)
{
}