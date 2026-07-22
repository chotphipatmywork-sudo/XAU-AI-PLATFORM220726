//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ExecutionContextBuilder.mqh                            |
//| Layer   : Core / Execution / Builder                             |
//| Version : 2.0.0                                                  |
//| Purpose : Build ExecutionContext from AI Decision                |
//+------------------------------------------------------------------+

#ifndef CORE_EXECUTION_BUILDER_EXECUTIONCONTEXTBUILDER_MQH
#define CORE_EXECUTION_BUILDER_EXECUTIONCONTEXTBUILDER_MQH

#include "../../ai/models/AIDecision.mqh"
#include "../../decision/models/DecisionResult.mqh"
#include "../models/ExecutionContext.mqh"


class CExecutionContextBuilder
{

public:

    bool Build(
        const CDecisionResult &decision,
        const string symbol,
        ENUM_TIMEFRAMES timeframe,
        CExecutionContext &context)
    {
        context.Reset();

        if(!decision.Valid || symbol=="")
            return false;

        MqlTick tick;
        if(!SymbolInfoTick(symbol,tick))
            return false;

        context.Decision=decision;
        context.Symbol=symbol;
        context.Timeframe=timeframe;
        context.Ask=tick.ask;
        context.Bid=tick.bid;
        context.Point=SymbolInfoDouble(symbol,SYMBOL_POINT);
        context.TickSize=SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_SIZE);
        context.Digits=(int)SymbolInfoInteger(symbol,SYMBOL_DIGITS);
        context.Spread=(context.Point>0.0 ?
                        (context.Ask-context.Bid)/context.Point : 0.0);
        context.Balance=AccountInfoDouble(ACCOUNT_BALANCE);
        context.Equity=AccountInfoDouble(ACCOUNT_EQUITY);
        context.FreeMargin=AccountInfoDouble(ACCOUNT_MARGIN_FREE);
        context.CurrentTime=TimeCurrent();

        return(context.Ask>0.0 &&
               context.Bid>0.0 &&
               context.Point>0.0);
    }


    bool Build(
        const CAIDecision &decision,
        CExecutionContext &context)
    {

        context.Reset();


        if(!decision.Valid)
            return false;



        context.Symbol =
            decision.Symbol;


        context.Timeframe =
            decision.Timeframe;



        if(decision.Action == AI_ACTION_BUY ||
           decision.Type == AI_DECISION_BUY)
        {
            context.Decision.Decision =
                DECISION_BUY;
        }
        else if(decision.Action == AI_ACTION_SELL ||
                decision.Type == AI_DECISION_SELL)
        {
            context.Decision.Decision =
                DECISION_SELL;
        }
        else
        {
            context.Decision.Decision =
                DECISION_WAIT;

            return false;
        }



        context.Decision.Confidence =
            decision.Confidence;


        context.Decision.Valid = true;



        return true;

    }

};


#endif
