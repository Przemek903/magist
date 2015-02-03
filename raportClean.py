raportStress = []
raportStrain = []

for an in range(1,21):
	raportStress.append('D:\\AbaqusWorkstation\\s%s.rpt' % an)
	raportStrain.append('D:\\AbaqusWorkstation\\le%s.rpt' % an)

liczba = 1

for rap in raportStrain:
        f = open(rap, 'r')
        lines = f.readlines()

        for nb in range(22):
                lines.pop(0)

        for nb in range(11):
                lines.pop(-1)

        a = lines.index('\n')
        for num in range(19):
                lines.pop(a)

        open('u' + str(liczba) + 'cl.rpt', 'w').writelines(lines)
        liczba += liczba

licz = 1
for rap in raportStress:
        f = open(rap, 'r')
        lines = f.readlines()

        for nb in range(22):
                lines.pop(0)

        for nb in range(11):
                lines.pop(-1)

        a = lines.index('\n')
        for num in range(19):
                lines.pop(a)

        open('s' + str(licz) + 'cl.rpt', 'w').writelines(lines)
        licz += licz




#with open('9mmdol.pickle') as f:
#    dispTable, stressTable, strainTable, coordTable, fileName, units, cycleTime, loads, elementTable, amplitudeTable, dateTable = pickle.load(f)
