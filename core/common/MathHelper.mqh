//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MathHelper.mqh                                         |
//| Layer   : Common                                                 |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_COMMON_MATHHELPER_MQH
#define CORE_COMMON_MATHHELPER_MQH

class CMathHelper
{
public:
    //--------------------------------------------------

    static double Clamp(
        const double value,
        const double minimum,
        const double maximum)
    {
        if (value < minimum)
            return minimum;

        if (value > maximum)
            return maximum;

        return value;
    }

    //--------------------------------------------------

    static double Average(
        const double a,
        const double b)
    {
        return (a + b) / 2.0;
    }

    //--------------------------------------------------

    static double Max(
        const double a,
        const double b)
    {
        return (a > b) ? a : b;
    }

    //--------------------------------------------------

    static double Min(
        const double a,
        const double b)
    {
        return (a < b) ? a : b;
    }

    //--------------------------------------------------

    static double Normalize(
        const double value,
        const int digits)
    {
        return NormalizeDouble(value, digits);
    }

    //--------------------------------------------------

    static double RoundToStep(
        const double value,
        const double step)
    {
        if (step <= 0.0)
            return value;

        return MathRound(value / step) * step;
    }

    //--------------------------------------------------

    static bool NearlyEqual(
        const double a,
        const double b,
        const double epsilon = 0.0000001)
    {
        return MathAbs(a - b) <= epsilon;
    }

    //--------------------------------------------------

    static bool IsZero(
        const double value,
        const double epsilon = 0.0000001)
    {
        return MathAbs(value) <= epsilon;
    }
};

#endif