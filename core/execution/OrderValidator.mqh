//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : OrderValidator.mqh                                     |
//| Layer   : Core / Execution                                       |
//| Version : 2.1.0                                                  |
//| Purpose : Validate Execution Result Before Trading               |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_ORDERVALIDATOR_MQH
#define CORE_EXECUTION_ORDERVALIDATOR_MQH

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"

//--------------------------------------------------

class COrderValidator
{
public:

   //--------------------------------------------------
   // Validate Result
   //--------------------------------------------------

   bool Validate(
      const CExecutionResult &result) const
   {
      if(!result.Success)
         return false;

      if(result.Status != EXECUTION_SUCCESS)
         return false;

      if(result.LotSize <= 0.0)
         return false;

      if(result.OrderType != ORDER_TYPE_BUY &&
         result.OrderType != ORDER_TYPE_SELL)
         return false;

      return true;
   }

   //--------------------------------------------------
   // Validate Context + Result
   //--------------------------------------------------

   bool Validate(
      const CExecutionContext &context,
      const CExecutionResult &result) const
   {
      if(context.Symbol == "")
         return false;

      if(!context.Decision.Valid)
         return false;

      return Validate(result);
   }

};

#endif