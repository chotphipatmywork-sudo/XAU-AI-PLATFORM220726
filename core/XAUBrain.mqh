//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : XAUBrain.mqh                                           |
//| Layer   : Core                                                   |
//| Version : 1.2.0                                                  |
//| Purpose : Central AI Platform                                    |
//+------------------------------------------------------------------+

#ifndef CORE_XAUBRAIN_MQH
#define CORE_XAUBRAIN_MQH

#include "market/MarketEngine.mqh"
#include "brain/Brain.mqh"
#include "brain/Context.mqh"
#include "risk/RiskEngine.mqh"
#include "execution/Execution.mqh"

//--------------------------------------------------
// XAU Brain
//--------------------------------------------------

class CXAUBrain
{
private:

   CMarketEngine Market;

   CBrain Brain;

   CRiskEngine Risk;

   CExecution Execution;

public:

   bool Process()
   {
      //--------------------------------------------------
      // Refresh Market
      //--------------------------------------------------

      if(!Market.Refresh())
         return false;

      //--------------------------------------------------
      // Build Context
      //--------------------------------------------------

      CContext context;

      //--------------------------------------------------
      // Think
      //--------------------------------------------------

      CDecision decision =
         Brain.Think(context);

      //--------------------------------------------------
      // Execute
      //--------------------------------------------------

      return Execution.Execute(decision);
   }
};

#endif