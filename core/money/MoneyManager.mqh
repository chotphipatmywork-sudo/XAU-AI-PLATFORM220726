//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MoneyManager.mqh                                       |
//| Layer   : Core / Money                                           |
//| Version : 1.2.0                                                  |
//| Purpose : Money Management + Risk Calculator                    |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_MONEYMANAGER_MQH
#define CORE_MONEY_MONEYMANAGER_MQH

#include "models/MoneyContext.mqh"
#include "models/MoneyResult.mqh"

#include "ExposureManager.mqh"
#include "RiskPerTradeCalculator.mqh"


class CMoneyManager
{
private:

    CExposureManager m_exposure;

    CRiskPerTradeCalculator m_riskCalculator;


public:


    bool RefreshExposure()
    {
        return m_exposure.Refresh();
    }



    double CurrentExposure()
    {
        return m_exposure.ExposurePercent();
    }



    bool CanTrade(double maxExposure)
    {
        return m_exposure.CanOpen(maxExposure);
    }



    CMoneyResult Calculate(
        const CMoneyContext &context)
    {
        CMoneyResult result;


        result.Valid = false;



        double riskMoney =
            m_riskCalculator.Calculate(
                context.Balance,
                context.RiskPercent);



        if(riskMoney <= 0.0)
        {
            result.LotSize = 0.01;
            return result;
        }



        if(context.StopLossPoints <= 0.0)
        {
            result.LotSize = 0.01;
            return result;
        }



        double tickValue =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_TRADE_TICK_VALUE);



        double tickSize =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_TRADE_TICK_SIZE);



        if(tickValue <= 0.0 || tickSize <= 0.0)
        {
            result.LotSize = 0.01;
            return result;
        }



        double pointValue =
            tickValue / tickSize;



        result.LotSize =
            riskMoney /
            (context.StopLossPoints * pointValue);



        double minLot =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_VOLUME_MIN);


        double maxLot =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_VOLUME_MAX);


        double stepLot =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_VOLUME_STEP);



        result.LotSize =
            MathMax(
                minLot,
                MathMin(
                    maxLot,
                    result.LotSize));



        result.LotSize =
            MathFloor(
                result.LotSize / stepLot)
            * stepLot;



        result.Valid = true;


        return result;
    }

};


#endif