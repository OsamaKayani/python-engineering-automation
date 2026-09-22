from anerkannt_ai import Module, compare, rank_candidates


def test_matching_exam_module_scores_above_unrelated_project():
    target=Module("Control Engineering",5,"control systems feedback stability", "exam")
    sources=[Module("Automation",5,"control systems feedback stability", "exam"),Module("CAD Project",5,"design assembly drawings", "project")]
    assert rank_candidates(sources,target)[0].source.name == "Automation"


def test_project_does_not_silently_cover_exam():
    source=Module("Automation Lab",5,"control systems feedback", "project")
    target=Module("Control Engineering",5,"control systems feedback", "exam")
    assert compare(source,target).assessment_compatible is False


def test_score_is_bounded():
    module=Module("Mathematics",5,"calculus linear algebra", "exam")
    assert compare(module,module).score == 100

