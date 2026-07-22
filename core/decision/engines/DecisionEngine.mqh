//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionEngine.mqh                                     |
//| Layer   : Core / Decision / Engine                               |
//| Version : 3.0.0                                                  |
//| Purpose : Decision Generation Engine                             |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_ENGINES_DECISIONENGINE_MQH
#define CORE_DECISION_ENGINES_DECISIONENGINE_MQH


#include "../models/DecisionContext.mqh"
#include "../models/DecisionResult.mqh"


//--------------------------------------------------
// Decision Engine
//--------------------------------------------------

class CDecisionEngine
{

public:


   //--------------------------------------------------
   // Generate Decision
   //--------------------------------------------------

   CDecisionResult Evaluate(
      const CDecisionContext &context)
   {

      CDecisionResult result;


      //--------------------------------------------------
      // Basic Validation
      //--------------------------------------------------

      if(!ValidateContext(context))
      {
         result.Reset();

         return result;
      }



      //--------------------------------------------------
      // Market Strength Calculation
      //--------------------------------------------------

      double score = 0.0;



      score +=
         context.Trend.Strength * 0.40;


      score +=
         context.Volatility.ExpansionScore * 0.20;


      score +=
         context.Liquidity.Score * 0.20;


      score +=
         context.Session.Confidence * 0.20;



   //--------------------------------------------------
// Decision Mapping
//--------------------------------------------------

if(score >= 70.0)
{

   result.Decision =
      DECISION_BUY;

}
else
if(score <= 30.0)
{

   result.Decision =
      DECISION_SELL;

}
else
{

   result.Decision =
      DECISION_WAIT;

}


result.Valid = true;


      return result;

   }



private:


   //--------------------------------------------------
   // Context Validation
   //--------------------------------------------------

   bool ValidateContext(
      const CDecisionContext &context)
   {

      if(context.Trend.Strength < 0)
         return false;


      if(context.Volatility.ExpansionScore < 0)
         return false;


      if(context.Liquidity.Score < 0)
         return false;


      if(context.Session.Confidence < 0)
         return false;



      return true;

   }

};


#endif

//+------------------------------------------------------------------+