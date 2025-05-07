using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FunctionApp.Model.InternetOfThings
{
    public class JointPositionModel
    {
        public double Base { get; set; }
        public double Shoulder { get; set; }
        public double Elbow { get; set; }
        public double Wrist1 { get; set; }
        public double Wrist2 { get; set; }
        public double Wrist3 { get; set; }
    }
}