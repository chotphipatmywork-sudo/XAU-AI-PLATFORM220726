//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeRequestBuilder.mqh                                |
//| Layer   : Core / Execution                                       |
//| Version : 2.2.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_TRADEREQUESTBUILDER_MQH
#define CORE_EXECUTION_TRADEREQUESTBUILDER_MQH

#include "models/ExecutionContext.mqh"
#include "models/ExecutionResult.mqh"

//--------------------------------------------------

class CTradeRequestBuilder
{
public:

   // รองรับโค้ดเดิม
   void Build(CExecutionResult &result)
   {
      if(result.LotSize <= 0.0)
         result.LotSize = 0.01;

      if(result.MagicNumber == 0)
         result.MagicNumber = 10001;

      if(result.Comment == "")
         result.Comment = "XAU AI PLATFORM";
   }

   // รองรับโค้ดใหม่
   void Build(
      const CExecutionContext &context,
      CExecutionResult &result)
   {
      Build(result);
   }
};

#endif