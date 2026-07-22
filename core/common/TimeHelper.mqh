//+------------------------------------------------------------------+

#ifndef CORE_COMMON_TIMEHELPER_MQH
#define CORE_COMMON_TIMEHELPER_MQH

class CTimeHelper
{
public:
    static int Hour()
    {
        MqlDateTime t;
        TimeToStruct(TimeCurrent(), t);
        return t.hour;
    }

    static int Minute()
    {
        MqlDateTime t;
        TimeToStruct(TimeCurrent(), t);
        return t.min;
    }

    static bool IsAsian()
    {
        int h = Hour();
        return (h >= 0 && h < 7);
    }

    static bool IsLondon()
    {
        int h = Hour();
        return (h >= 7 && h < 13);
    }

    static bool IsNewYork()
    {
        int h = Hour();
        return (h >= 13 && h < 22);
    }

    static bool IsWeekend()
    {
        MqlDateTime t;
        TimeToStruct(TimeCurrent(), t);

        return (t.day_of_week == 0 || t.day_of_week == 6);
    }
};

#endif