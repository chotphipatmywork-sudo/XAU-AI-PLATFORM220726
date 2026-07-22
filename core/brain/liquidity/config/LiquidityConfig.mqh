//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityConfig.mqh                                    |
//| Layer   : Brain / Liquidity / Config                             |
//| Version : 1.0.0                                                  |
//| Purpose : Configuration for Liquidity Package                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_CONFIG_LIQUIDITYCONFIG_MQH
#define CORE_BRAIN_LIQUIDITY_CONFIG_LIQUIDITYCONFIG_MQH

class CLiquidityConfig
{
public:
    int SwingLookback;

    double EqualHighTolerance;

    double SweepTolerance;

    CLiquidityConfig()
    {
        SwingLookback = 10;

        EqualHighTolerance = 5.0;

        SweepTolerance = 2.0;
    }
};

#endif