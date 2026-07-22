//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionContext.mqh                                   |
//| Layer   : Core / Execution / Models                              |
//| Version : 2.1.0                                                  |
//| Purpose : Execution Input Context                                |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_MODELS_EXECUTIONCONTEXT_MQH
#define CORE_EXECUTION_MODELS_EXECUTIONCONTEXT_MQH

#include "../../decision/models/DecisionResult.mqh"

//--------------------------------------------------
// Execution Context
//--------------------------------------------------

class CExecutionContext
{
public:

   //--------------------------------------------------
   // Decision
   //--------------------------------------------------

   CDecisionResult Decision;

   //--------------------------------------------------
   // Symbol
   //--------------------------------------------------

   string Symbol;

   ENUM_TIMEFRAMES Timeframe;

   //--------------------------------------------------
   // Market
   //--------------------------------------------------

   double Ask;

   double Bid;

   double Spread;

   double Point;

   double TickSize;

   int Digits;

   //--------------------------------------------------
   // Account
   //--------------------------------------------------

   double Balance;

   double Equity;

   double FreeMargin;

   //--------------------------------------------------
   // Time
   //--------------------------------------------------

   datetime CurrentTime;

public:

   //--------------------------------------------------

   CExecutionContext()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Decision.Reset();

      Symbol = "";

      Timeframe = PERIOD_CURRENT;

      Ask = 0.0;

      Bid = 0.0;

      Spread = 0.0;

      Point = 0.0;

      TickSize = 0.0;

      Digits = 0;

      Balance = 0.0;

      Equity = 0.0;

      FreeMargin = 0.0;

      CurrentTime = 0;
   }
};

#endif