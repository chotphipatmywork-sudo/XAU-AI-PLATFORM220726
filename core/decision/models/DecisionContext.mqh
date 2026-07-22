//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionContext.mqh                                    |
//| Layer   : Core / Decision / Models                               |
//| Version : 3.0.0                                                  |
//| Purpose : Decision Input Context                                 |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_MODELS_DECISIONCONTEXT_MQH
#define CORE_DECISION_MODELS_DECISIONCONTEXT_MQH


#include "../../brain/trend/models/TrendResult.mqh"

#include "../../brain/volatility/models/VolatilityResult.mqh"

#include "../../brain/liquidity/models/LiquidityResult.mqh"

#include "../../brain/session/models/SessionResult.mqh"


//--------------------------------------------------
// Decision Context
//--------------------------------------------------

class CDecisionContext
{

public:


   //--------------------------------------------------
   // Brain Analysis Input
   //--------------------------------------------------

   CTrendResult Trend;


   CVolatilityResult Volatility;


   CLiquidityResult Liquidity;


   CSessionResult Session;



public:


   //--------------------------------------------------

   CDecisionContext()
   {
      Reset();
   }



   //--------------------------------------------------

   void Reset()
   {

      Trend.Reset();


      Volatility.Reset();


      Liquidity.Reset();


      Session.Reset();

   }

};


#endif

//+------------------------------------------------------------------+